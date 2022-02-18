import enum


class StatusEnum(enum.Enum):
    NOTFOUND = 'File at provided link was not found.'
    NOTAWEBM = 'File at provided link is not a WebM.'
    FAILED = 'Conversion failed.'
    TIMEOUT = 'Conversion took too long.'
    SUCCESS = 'Success.'
