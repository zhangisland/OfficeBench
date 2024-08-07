import docker, time
from loguru import logger
import os
import os.path as osp


def build_docker(docker_image_name, dockerfile_path):
    """
    Build the docker image for the InterCode Bash environment. If the image already exists, do nothing.
    """
    client = docker.from_env()
    available_images = [y for x in client.images.list() for y in x.tags]
    logger.info(f"Available local docker images: {available_images}")
    if f"{docker_image_name}:latest" in available_images:
        return
    logger.info(f"`{docker_image_name}:latest` not in list of available local docker images, building...")
    
    client.images.build(
        path=osp.join(os.getcwd(), "docker"),
        dockerfile=dockerfile_path,
        tag=docker_image_name,
        rm=True,
        nocache=True
    )

    # Give some time for Bash server to start
    logger.info("✓ Bash Docker image built successfully. " + \
          "Waiting for 5 seconds for Bash container to start...\n" + \
         f"If you encounter an error, run `docker ps --all` and check if `{docker_image_name}` conatiners were created. " + \
          "Container start up time varies by machine.")
    time.sleep(5)


