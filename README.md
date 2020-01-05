# Azure Functions: SeriviceTags (Public) API

[Azure でホストされている IP アドレス一覧](https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519) を収集し、取得するための Azure Functions

## get-servicetags-public-json

HTTP トリガーのファンクションで、json ファイルを取得する API (Web API) を提供する。

`CONNECT_STR` で指定された Azure Blob Storage の、`CONTAINER_NAME` 内に保存されている ServiceTags の最新 JSON を取得する。
なお、`CONNECT_STR` および `CONTAINER_NAME` はどちらも環境変数で指定されている。

## servicetags-public-json-crawler

CRON でスケジュール実行されるファンクション。
JSON ファイルを BLOB ストレージに毎日収集する。