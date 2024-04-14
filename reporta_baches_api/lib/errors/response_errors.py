from rest_framework.response import Response


class ResponseError():
    def __init__(self, cd=0, msg: str = ''):
        self.code = cd
        self.message = msg
        self.details = []

    def add_error(self, code=0, message: str = ""):
        err = ResponseError(code, message)
        self.details.append(err)

    @classmethod
    def build_single_error(cls, status_error_code, detail_code, message: str):
        """
        Will build an error messsage with just one detail
        """
        error = ResponseError(status_error_code, message)
        error.add_error(detail_code, message)
        return error

    def get_response(self):
        if len(self.details) > 0:
            details = [x.get_response() for x in self.details]
            d = {'error': {'code': self.code, 'message': self.message, 'detail': details}}
            return Response(d, status=self.code)

        return {'key': self.code, 'message': self.message}

    def get_response_body(self):
        if len(self.details) > 0:
            details = [x.get_response() for x in self.details]
            d = {'error': {'code': self.code, 'message': self.message, 'detail': details}}
            return d

        return {'key': self.code, 'message': self.message}