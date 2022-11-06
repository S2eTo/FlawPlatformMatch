import base64

import docker
from django.conf import settings
from datetime import datetime, timedelta
from apscheduler.jobstores.base import JobLookupError
from docker.errors import NotFound as DockerNotFoundErrors
from apscheduler.schedulers.background import BackgroundScheduler


class DockerApi(object):

    def __init__(self):
        self.client = docker.DockerClient(base_url=settings.DOCKER_API.get('URL'), timeout=3)

        # 启动即使任务
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def run_container(self, image_id, expose: str, flag: str, flag_style: int, flag_file_path: str = None,
                      flag_format: str = '{}'):
        """
        启动容器/靶机
        """

        ports = {}
        exposes = expose.split(',')
        for port in exposes:
            port = port.strip()
            ports[port] = settings.DOCKER_API.get('PUBLIC_PORT_RANG')

        container = None

        if flag_style == 1:
            container = self.client.containers.run(image_id, ports=ports, detach=True, environment={
                settings.DOCKER_API.get('FLAG_ENVIRONMENT_NAME'): flag
            })
        elif flag_style == 2:
            container = self.client.containers.run(image_id, ports=ports, detach=True)
            file_content = base64.b64encode(flag_format.replace("{FLAG}", flag).encode())
            cmd = f"/bin/bash -c \"echo '{file_content.decode()}' | base64 -d > '{flag_file_path}'\""
            container.exec_run(cmd=cmd)
        elif flag_style == 3:
            container = self.client.containers.run(image_id, ports=ports, detach=True)

        if container is None:
            raise Exception("好好录题！别给我整这些有的没的！")

        # 重新获取容器, 因为映射端口是随机的。启动后返回的容器对象中是没有端口信息
        container = self.client.containers.get(container_id=container.id)

        # 解析端口样式
        p = ""
        for key in container.ports:
            item = container.ports[key]
            for expose in item:
                p += settings.DOCKER_API.get('EXTERNAL_URL') + ":" + expose['HostPort'] + ","
            p = p[:len(p) - 1]
            p += "->" + key + ", "

        setattr(container, "public_port", p[:len(p) - 2])

        return container

    def stop_container(self, container_id):
        """
        停止并删除容器/靶机
        """

        try:
            container = self.client.containers.get(container_id=container_id)
        except DockerNotFoundErrors as e:
            return

        container.stop()
        # 阻塞等待
        # container.wait()

        # 删除容器
        container.remove()

    def create_scheduler(self, container):
        """
        创建定时任务, 1 小时后删除容器
        """
        #
        try:
            job = self.scheduler.add_job(container.delete, 'date',
                                         run_date=datetime.now() + timedelta(
                                             hours=settings.DOCKER_API.get('AUTO_REMOVE_CONTAINER')))
            return job
        except Exception:
            self.stop_container(container.id)

        return None

    def remove_scheduler_job(self, job_id):
        """
        删除指定定时任务
        """
        try:
            self.scheduler.remove_job(job_id)
        except JobLookupError:
            pass

    def delete(self, container_id, job_id):
        """
        删除指定定时任务与容器
        """

        self.stop_container(container_id=container_id)
        self.remove_scheduler_job(job_id)

    def get_images(self, image_id):
        return self.client.images.get(image_id)


docker_api = DockerApi()
