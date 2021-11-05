#!/usr/bin/env python
# coding:UTF-8
# author:keqi time:2021/11/04

from pathlib import Path
import paramiko
from ReadFileList import *

class Pdf_2_SFTP:
    # 记录第一个被创建对象的引用
    instance = None
    # 记录是否执行过初始化动作
    init_flag = False

    def __new__(cls, *args, **kwargs):
        # 1.判断类属性是否为空对象，若为空说明第一个对象还没被创建
        if cls.instance is None:
            # 2.对第一个对象没有被创建，我们应该调用父类的方法，为第一个对象分配空间
            cls.instance = super().__new__(cls)
        # 3.把类属性中保存的对象引用返回给python的解释器
        return cls.instance

    def __init__(self, readFileList):
        # 1.判断是否执行过初始化动作,若执行过，直觉return
        if Pdf_2_SFTP.init_flag:
            return
        self.readFileList = readFileList
        self.ssh = None
        Pdf_2_SFTP.init_flag = True

    def getTransport(self):
        self.ssh = paramiko.SSHClient()  # 创建SSH对象
        linux_ip = self.readFileList.getConfigByKey("ww-database", "linux_ip")
        linux_port = self.readFileList.getConfigByKey("ww-database", "linux_port")
        linux_username = self.readFileList.getConfigByKey("ww-database", "linux_username")
        linux_password =  self.readFileList.getConfigByKey("ww-database", "linux_password")
        linux_private_key = self.readFileList.getConfigByKey("ww-database", "linux_private_key")

        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 允许连接不在know_hosts文件中的主机
        transport = paramiko.Transport((linux_ip, int(linux_port)))
        if linux_private_key:
            private_key = paramiko.RSAKey.from_private_key_file(linux_private_key)  # 指定私钥
            transport.connect(username=linux_username, password=linux_password, pkey=private_key)  # 连接服务器
        else:
            transport.connect(username=linux_username, password=linux_password)  # 连接服务器

        return transport

    # 上传文件到SFTP
    def uploadPdf(self, local_file_path, upload_file_path):
        upload_path = upload_file_path  # 上传服务器文件路径
        if not upload_file_path:
            upload_path = self.readFileList.getConfigByKey("ww-database", "linux_sftp_file_path")

        local_path = local_file_path   # 本地上传图片路径
        if not local_path:
            imagepath = self.readFileList.getConfigByKey("file", "imagepath")
            if imagepath:
                local_path = imagepath
            else:
                imagepath = self.readFileList.getConfigByKey("file", "filepath")
                path = Path(imagepath)
                local_path = str(path.parent.absolute()) + os.sep + "image"
                # 判断文件或文件夹是否存在可以用来安全的创建文件
                Path(local_path).mkdir(parents=True, exist_ok=True)

        sftp = paramiko.SFTPClient.from_transport(self.getTransport())
        try:
            for file in Path(local_path).iterdir():
                file_name = file.name.replace("-", "")
                # 判断当前日期文件夹是否存在
                is_existence = True if file_name in sftp.listdir(upload_path) else False
                new_upload_path = upload_path
                if not is_existence:
                    new_upload_path = upload_path + "/" + file_name
                    # 创建文件夹
                    sftp.mkdir(upload_path + "/" + file_name)
                if not str(new_upload_path).endswith("/" + file_name):
                    new_upload_path = upload_path + "/" + file_name
                    # 创建文件夹
                    sftp.mkdir(upload_path + "/" + file_name)

                for real_file in self.readFileList.resFileListByPath(file, ".jpg"):
                    print(new_upload_path + '/' + Path(real_file).name)
                    sftp.put(real_file, new_upload_path + '/' + Path(real_file).name)
                print('SFTP上传成功')
        except Exception as e:
            print(e)
        self.ssh.close()

if __name__ == '__main__':
    readFileList = ReadFileList()
    pdf_2_SFTP = Pdf_2_SFTP(readFileList)
    pdf_2_SFTP.uploadPdf(None, None)