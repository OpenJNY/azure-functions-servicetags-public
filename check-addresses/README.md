# check-addresses

指定した IP アドレス (複数入力可) を含むサービスタグを出力する。 

## API Usage

### Request

- HTTP Method: `POST`
- Body: JSON

  ```json
  {
    "addresses": [
      "<ipv4-address-1>",
      "<ipv4-address-2>",
      "<ipv4-address-3>",
    ]
  }
  ```


Linux

```bash
curl -X POST -H 'Content-Type:application/json' -d '{"addresses": ["1.1.1.1", "2.2.2.2"]}' https://<functionapp-name>.azurewebsites.net/api/check-addresses
```

Windows

``` powershell
$body = @{addresses=@("1.1.1.1", "104.40.128.30")} | ConvertTo-Json
$uri = "https://<functionapp-name>.azurewebsites.net/api/check-addresses"

$response = Invoke-RestMethod -Method POST -Uri $uri -Body $body -ContentType application/json
$response.results | foreach { echo $_.address; echo $_.servicetags }
```

### Response

```json
{
  "message": "メッセージ",
  "json": "使われた json ファイル",
  "results": [
    {
      "address": "1つ目のアドレス",
      "servicetags": 結果のリスト
    },

  ]
}
```

example

```json
{
    "message": "success",
    "json": "ServiceTags_Public_20191216.json",
    "results": [
        {
            "address": "1.1.1.1",
            "servicetags": []
        },
        {
            "address": "104.40.128.30",
            "servicetags": [
                {
                    "name": "AzureCloud.westeurope",
                    "id": "AzureCloud.westeurope",
                    "changeNumber": 25,
                    "region": "westeurope",
                    "platform": "Azure",
                    "systemService": "",
                    "addressPrefix": "104.40.128.0/17"
                },
                {
                    "name": "AzureCloud",
                    "id": "AzureCloud",
                    "changeNumber": 75,
                    "region": "",
                    "platform": "Azure",
                    "systemService": "",
                    "addressPrefix": "104.40.128.0/17"
                }
            ]
        }
    ]
}
```