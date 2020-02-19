from telegram import Update
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CallbackContext

from face_rec.config import TG_TOKEN

import cv2 as cv
from skimage import io

# Creating OpenCV CascadeClassifier
face_cascade_name = 'haarcascade_frontalface_default.xml'
face_cascade = cv.CascadeClassifier(face_cascade_name)


# Function for checking if there is a face in the photo
def is_face(frame):
    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame_gray = cv.equalizeHist(frame_gray)
    faces = face_cascade.detectMultiScale(frame_gray, 1.3, 6)
    return len(faces) != 0


def do_start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Hello! Send me a photo',
    )


# When a user sends a photo, check if there is a face and download it if there is one.
def download_if_face_found(update: Update, context: CallbackContext):
    photo_id = update.message.photo[-1].file_id
    photo_file = context.bot.get_file(photo_id)
    file_path = photo_file.file_path
    photo = io.imread(file_path)

    download_dir = './media/'

    face_detected = is_face(photo)

    if face_detected:
        text = 'Face detected'
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=text,
        )

        try:
            photo_file.download(download_dir + photo_id + '.jpg')
            text = 'File successfully downloaded'
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=text,
            )
        except ValueError:
            text = 'Failed to download file'
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=text,
            )
    else:
        text = 'No face detected'
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=text,
        )


def main():
    # Creating bot
    updater = Updater(
        token=TG_TOKEN,
        use_context=True,
    )

    # Creating handlers
    start_handler = CommandHandler('start', do_start)
    photo_message_handler = MessageHandler(Filters.photo, download_if_face_found)

    # Adding handlers
    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(photo_message_handler)

    # Start bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
