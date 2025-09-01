# AliyunOSS_CertUpdate

自动化更新阿里云 OSS 自定义域名证书的解决方案。

## 项目简介
本项目通过 GitHub Actions 自动申请 Let's Encrypt 证书，并将新证书自动绑定到阿里云 OSS 的自定义域名，实现证书自动续期和更新。

## 主要文件说明
- `oss_update.py`：核心脚本，负责将新证书绑定到 OSS Bucket 的自定义域名。
- `alidns.sh`：用于 certbot DNS 验证的钩子脚本。
- `.github/workflows/alioss-update-auto.yml`：GitHub Actions 工作流，自动化申请证书并更新 OSS 证书。

## 阿里云 ACCESS KEY 权限说明（偷懒版）
在 阿里云 [RAM 访问控制](https://ram.console.aliyun.com/users)中新建用户，并添加权限
 - AliyunOSSFullAccess 管理对象存储服务（OSS）权限
 - AliyunYundunCertFullAccess 管理云盾证书服务的权限
 - AliyunDNSFullAccess 管理云解析（DNS）的权限

## 使用方法
### 1. 配置 Secrets
在 GitHub 仓库的 Settings > Secrets 中添加以下密钥：
- `ACCESS_KEY_ID`：阿里云 AccessKeyId
- `ACCESS_KEY_SECRET`：阿里云 AccessKeySecret
- `ENDPOINT`：OSS Endpoint，例如 `oss-cn-hangzhou.aliyuncs.com`
- `BUCKET_NAME`：OSS Bucket 名称， 例如 `example-bucket`
- `DOMAIN`：需要绑定证书的自定义域名（如 `oss.example.com`）
- `REGION`：阿里云区域（如 `cn-hangzhou`）
- `EMAIL`：用于申请证书的邮箱

### 2. 工作流自动执行
每周日自动执行，也可手动触发。流程如下：
1. 申请新的 Let's Encrypt 证书，证书文件保存于 `/etc/letsencrypt/live/$DOMAIN/`。
2. 读取 `fullchain.pem` 和 `privkey.pem`，自动传递给 `oss_update.py`。
3. `oss_update.py` 自动将新证书绑定到 OSS Bucket 的自定义域名。

### 3. 手动运行脚本
如需本地手动运行：
```bash
pip install -r requirements.txt
python oss_update.py \
  --access-key-id <你的AccessKeyId> \
  --access-key-secret <你的AccessKeySecret> \
  --endpoint <你的Endpoint> \
  --bucket-name <你的Bucket名称> \
  --target-cname <你的自定义域名> \
  --private-key "$(cat /etc/letsencrypt/live/<你的域名>/privkey.pem)" \
  --certificate "$(cat /etc/letsencrypt/live/<你的域名>/fullchain.pem)"
```

## 注意事项
- 证书和私钥文件需有读取权限。
- 阿里云账号需有 OSS 管理权限。
- 建议定期检查 workflow 执行结果。

## 致谢
感谢 [hui-shao/AliyunOSS_Cert_Update](https://github.com/hui-shao/AliyunOSS_Cert_Update) 提供的 OSS 证书上传教程。
感谢 [justjavac/certbot-dns-aliyun](https://github.com/justjavac/certbot-dns-aliyun) 的证书申请教程。

## License
MIT
