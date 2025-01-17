from enum import Enum


class UserStep(Enum):
    START = 1

class UserStatus(Enum):
    ACTIVE = 'active'
    PASSIVE = 'passive'

class ResourcesType(Enum):
    TEXT = 'text'
    PHOTO = 'photo'
    VIDEO = 'video'
    DOCUMENT = 'document'
    AUDIO = 'audio'
    VOICE = 'voice'
    VIDEO_NOTE = 'video_note'
