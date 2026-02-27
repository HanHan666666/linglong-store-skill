# ll-cli 命令参考

## 安装

- 基本安装：ll-cli install <appid>
- 指定版本：ll-cli install <appid/version>
- 指定模块：ll-cli install <appid> --module=<module>
- 指定仓库：ll-cli install <appid> --repo=<repo>
- 强制指定版本：ll-cli install <appid> --force
- 自动确认：ll-cli install <appid> -y
- 文件安装：ll-cli install <path>.uab 或 ll-cli install <path>.layer

## 升级

- 升级所有：ll-cli upgrade
- 升级单个：ll-cli upgrade <appid>

## 列表与卸载

- 已安装列表：ll-cli list
- 卸载：ll-cli uninstall <appid>

## 禁用本地搜索

- 在线搜索必须使用 Web API
- 不使用 ll-cli search
