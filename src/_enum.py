import enum


class StatusEnum(enum.Enum):
    NOTFOUND = 'Provided file was not found.'
    NOTAWEBM = 'Provided file is not a WebM.'
    NOTAURL = 'Provided string is not a URL.'
    FAILED = 'Conversion failed.'
    TIMEOUT = 'Conversion took too long.'
    SUCCESS = 'Success.'
