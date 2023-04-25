from wtforms import ValidationError


def image_validator(form, field):
    if field.data and field.data.filename.split(".")[-1] not in ["png", "jpg", "jpeg", "webp"]:
        raise ValidationError("Файл не соответствует формату!")


def video_validator(form, field):
    if field.data and field.data.filename.split(".")[-1] not in ["mp4", "webm", "avi"]:
        raise ValidationError("Файл не соответствует формату!")
