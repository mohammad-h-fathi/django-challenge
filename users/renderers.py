from rest_framework.renderers import JSONRenderer


class ApiRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code
        response_dict = {
            'status': 200,
            'data': None,
            'message': None,
        }
        if not data:
            if status_code == 204:
                response_dict['message'] = 'Deleted Successfully'
                response_dict['status'] = 204
            return super(ApiRenderer, self).render(response_dict, accepted_media_type, renderer_context)
        if isinstance(data, list):
            response_dict = {
                'status': 200,
                'data': data,
                'message': None,
            }
        else:
            if data.get('data'):
                response_dict['data'] = data.get('data')
            elif status_code < 400 and data.get('data') is None:
                response_dict['data'] = data
            if data.get('status'):
                response_dict['status'] = data.get('status')
            else:
                response_dict['status'] = status_code
            if data.get('message'):
                response_dict['message'] = data.get('message')
            elif data.get('detail'):
                if isinstance(data.get('detail'), dict):
                    response_dict['message'] = data.get('detail')
                else:
                    response_dict['message'] = {'general': data.get('detail')}
            elif status_code > 399:
                response_dict['message'] = data

        return super(ApiRenderer, self).render(response_dict, accepted_media_type, renderer_context)
