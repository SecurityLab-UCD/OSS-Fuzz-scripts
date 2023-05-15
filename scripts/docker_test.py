import docker
import os

client = docker.from_env()
# List all images on the system
images = client.images.list()

proj_name = 'eigen'
file_path = '/src/basicstuff_fuzzer'
image = client.images.get('gcr.io/oss-fuzz/'+proj_name+':latest')
print(image)

# Print the details of each image
# for image in images:
#     if image.tags!=[] and 'zlib' in image.tags[0]:
#         print("Image ID:", image.id)
#         print("Tags:", image.tags)
#         print("Size:", image.attrs['Size'], "bytes")
#         print()
        
# Create a container from the image
# container = client.containers.create(image=image)
container=client.containers.run(image,detach=True)


for chunk in container.get_archive(file_path+'.cc')[0]:
    print(chunk.decode('utf-8'))
# Stop and remove the container
container.stop()
container.remove()