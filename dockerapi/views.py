import json
from docker.errors import ImageNotFound

from dockerapi.api import docker_api
from common.views import AdministratorAPIView, CheckGetPermissionsAPIView


class GetImage(AdministratorAPIView, CheckGetPermissionsAPIView):

    def get(self, request):
        image_id = str(request.GET.get('id')).strip()
        try:
            image = docker_api.get_images(image_id)
        except ImageNotFound:
            return self.failed("未找到相应镜像", status=404)

        return self.success("获取成功", data={'id': image.id, 'short_id': image.short_id, 'tags': image.tags,
                                          'labels': image.labels,
                                          'expose_ports': json.loads(json.dumps(
                                              image.attrs['Config']['ExposedPorts'])
                                          ), })
