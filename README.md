# レース結果作成
### 概要
書け

### How To Deploy

```
gcloud pubsub topics create betting_result_topic
```

```
gcloud functions deploy create_betting_result \
--trigger-topic betting_result_topic \
--runtime python39 \
--entry-point main \
--timeout 540 \
--region asia-northeast1
```

```
gcloud beta scheduler jobs create pubsub betting_result_exec_every10min \
--schedule "*/10 9-23 * * *" \
--topic betting_result_topic \
--time-zone 'Asia/Tokyo'
```