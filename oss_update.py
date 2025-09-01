import sys
import argparse
from datetime import datetime, timezone

import oss2
from oss2.models import CnameInfo

class OSS:
    def __init__(self, access_key_id: str, access_key_secret: str, endpoint: str, bucket_name: str, region: str = "cn-hangzhou"):
        self.auth = oss2.AuthV4(access_key_id, access_key_secret)
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.region = region
        self.bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name=self.bucket_name, region=self.region)

    def run_update(self, target_cname: str, private_key: str, certificate: str):
        cname_info = self._get_matched_cname(target_cname)
        if cname_info and private_key and certificate:
            self._update_cname(cname_info, private_key, certificate)
        else:
            print("未找到匹配的自定义域名或证书信息不完整")
            sys.exit(1)

    def _get_matched_cname(self, target_cname: str) -> CnameInfo | None:
        cname_list = self._get_cname_info()
        for c in cname_list:
            if c.domain == target_cname:
                return c
        return None

    def _get_cname_info(self, isprint: bool = False) -> list:
        list_result = self.bucket.list_bucket_cname()
        if isprint:
            for c in list_result.cname:
                print(f"证书 ID ： {getattr(c.certificate, 'cert_id', None)}")  # 打印证书ID
                print(f"自定义域名： {c.domain}")  # 打印自定义域名
                print(f"最后修改时间： {c.last_modified}")  # 打印绑定自定义域名的时间
        return list_result.cname

    def _update_cname(self, cname_info: CnameInfo, private_key: str, certificate: str):
        # 检查是否已绑定证书和证书是否过期
        create_new_cert = True  # 默认创建一个新的证书
        if cname_info.certificate:
            exp_date_obj = datetime.strptime(
                cname_info.certificate.valid_end_date,
                '%b %d %H:%M:%S %Y GMT'
            ).replace(tzinfo=timezone.utc)
            if exp_date_obj > datetime.now(timezone.utc):  # 证书未过期
                create_new_cert = False

        if create_new_cert:  # 如果没有绑定证书，直接传入证书内容，会创建一个新的证书
            print("证书已过期或未绑定证书，将创建新的证书")
            cert = oss2.models.CertInfo(certificate=certificate, private_key=private_key, force=True)
        else:  # 如果已经绑定了证书且证书未过期
            print("证书未过期，将更新证书。当前证书信息如下：")
            print(vars(cname_info.certificate))
            cert = oss2.models.CertInfo(previous_cert_id=cname_info.certificate.cert_id,
                                        certificate=certificate, private_key=private_key, force=True)

        input_ = oss2.models.PutBucketCnameRequest(cname_info.domain, cert)
        self.bucket.put_bucket_cname(input_)


def main():
    parser = argparse.ArgumentParser(description="Aliyun OSS 证书自动更新脚本")
    parser.add_argument('--access-key-id', required=True, help='阿里云 AccessKeyId')
    parser.add_argument('--access-key-secret', required=True, help='阿里云 AccessKeySecret')
    parser.add_argument('--endpoint', required=True, help='OSS Endpoint')
    parser.add_argument('--bucket-name', required=True, help='OSS Bucket 名称')
    parser.add_argument('--target-cname', required=True, help='需要更新证书的自定义域名')
    parser.add_argument('--private-key', required=True, help='证书私钥内容')
    parser.add_argument('--certificate', required=True, help='证书内容')
    parser.add_argument('--region', default='cn-hangzhou', help='OSS 区域，默认为 cn-hangzhou')

    args = parser.parse_args()

    oss = OSS(
        access_key_id=args.access_key_id,
        access_key_secret=args.access_key_secret,
        endpoint=args.endpoint,
        bucket_name=args.bucket_name,
        region=args.region
    )
    oss.run_update(args.target_cname, args.private_key, args.certificate)


if __name__ == "__main__":
    main()
