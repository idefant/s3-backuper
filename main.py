import io
import zipfile
import os
import yaml
import boto3
import datetime


def get_zipped_dir(path):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zipper:
        for dirname, subdirs, files in os.walk(path):
            for filename in files:
                filepath = os.path.relpath(os.path.join(dirname, filename), start=path)
                zipper.write(os.path.join(dirname, filename), arcname=filepath)
    zip_buffer.seek(0)
    return zip_buffer


def archive_files():
    with open('config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

        s3 = boto3.client(
            service_name='s3',
            endpoint_url=config['s3']['url'],
            region_name=config['s3']['region'],
            aws_access_key_id=config['s3']['username'],
            aws_secret_access_key=config['s3']['password'],
        )

        for dir in config['dirs']:
            zip_buffer = get_zipped_dir(dir['path'])
            formatted_date = datetime.date.today().strftime('%Y-%m-%d')
            file_key = f"{dir['key_prefix']}/{formatted_date}.zip"
            s3.upload_fileobj(zip_buffer, config['s3']['bucket'], file_key)


if __name__ == '__main__':
    archive_files()
