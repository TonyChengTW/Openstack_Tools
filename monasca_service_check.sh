#!/bin/sh

## test
set -o xtrace
TOP_DIR=$(cd $(dirname "$0") && pwd)
LOG_TIME_FMT="%F %H:%M:%S"
timestamp()
{
  date "+$LOG_TIME_FMT"
}
echo "$(timestamp) : Working directory in $TOP_DIR"

echo `date -u +"%Y-%m-%dT%H:%M:%SZ"`

export KEYSTONE_API_HOST="192.168.8.91"
export MONASCA_API_HOST="192.168.8.71"
export HOST_NAME=`hostname`

## Keystone authentication ##
cat > token-request.json << EOF
{
  "auth": {
    "identity": {
      "methods": [
        "password"
      ],
      "password": {
        "user": {
          "domain": {
            "name": "Default"
          },
          "name": "mini-mon",
          "password": "password"
        }
      }
    },
    "scope": {
      "project": {
        "domain": {
          "name": "Default"
        },
        "name": "mini-mon"
      }
    }
  }
}
EOF

export TOKEN=`curl -si -d @token-request.json -H "Content-type: application/json" http://${KEYSTONE_API_HOST}:5000/v3/auth/tokens | awk '/X-Subject-Token/ {print $2}' | tr -d '\r'`
echo "Keystone-API http://${KEYSTONE_API_HOST}:5000/v3"
echo "> TOKEN: $TOKEN"
echo

## Use metrics and dimension by Monasca-API ##
echo "Monasca-API http://${MONASCA_API_HOST}:8070/v2.0"
echo "> GET metrics"
curl -sS -H X-Auth-Token:${TOKEN} -H "Content-Type: application/json" http://${MONASCA_API_HOST}:8070/v2.0/metrics | python -m json.tool
echo

echo "> POST metrics"
TIMESTAMP=`date +%s`000.00
PAYLOAD='[{"name": "cpu.system_perc", "dimensions": {"hostname": "'${HOST_NAME}'"}, "value": 0.22, "value_meta": null, "timestamp": '${TIMESTAMP}'}]'
echo "> PAYLOAD: ${PAYLOAD}"
curl -sS -i -X POST -H X-Auth-Token:${TOKEN} -H "Content-Type:application/json" -d "${PAYLOAD}" http://${MONASCA_API_HOST}:8070/v2.0/metrics
echo

echo "> GET metrics/names"
curl -sS -H X-Auth-Token:${TOKEN} -H "Content-Type:application/json" http://${MONASCA_API_HOST}:8070/v2.0/metrics/names | python -m json.tool
echo

echo "> GET metrics/dimension/names"
curl -sS -H X-Auth-Token:${TOKEN} -H "Content-Type:application/json" http://${MONASCA_API_HOST}:8070/v2.0/metrics/dimensions/names | python -m json.tool
echo

echo "> GET metrics/dimension/names/values?dimension_name=hostname"
curl -sS -H X-Auth-Token:${TOKEN} -H "Content-Type:application/json" http://${MONASCA_API_HOST}:8070/v2.0/metrics/dimensions/names/values?dimension_name=hostname | python -m json.tool
echo

echo "> POST logs"
PAYLOAD='{"dimensions":{"hostname":"'${HOST_NAME}'","service":"monitoring"},"logs":[{"message":"'${TIMESTAMP}' this is mysql log","dimensions":{"component":"mysql","path":"/var/log/mysql.log"}},{"message":"'${TIMESTAMP}' this is monasca-api log","dimensions":{"component":"monasca-api","path":"/var/log/monasca/monasca-api.log"}}]}'
echo "> PAYLOAD: ${PAYLOAD}"
curl -sS -i -X POST -H X-Auth-Token:${TOKEN} -H "Content-Type:application/json" -d "${PAYLOAD}" http://${MONASCA_API_HOST}:8070/v2.0/logs
echo 

## Use measurements and statistics by Monasca-API ##
START_TIME=`date -u +"%Y-%m-%dT00:00:00Z"`

echo "> GET metrics/measurements?name=cpu.system_perc&start_time=${START_TIME}&merge_metrics=True"
curl -sS -H X-Auth-Token:${TOKEN} -H "Content-Type: application/json" "http://${MONASCA_API_HOST}:8070/v2.0/metrics/measurements?name=cpu.system_perc&start_time=${START_TIME}&merge_metrics=True" | python -m json.tool
echo

echo "> GET metrics/measurements?name=cpu.system_perc&start_time=${START_TIME}&merge_metrics=True"
curl -sS -H X-Auth-Token:${TOKEN} -H "Content-Type: application/json" "http://${MONASCA_API_HOST}:8070/v2.0/metrics/measurements?name=cpu.system_perc&start_time=${START_TIME}&dimensions=hostname:${HOST_NAME}" | python -m json.tool
echo

echo "> GET metrics/statistics?name=cpu.system_perc&merge_metrics=True&statistics=avg,min,max,sum,count&period=3600"
curl -sS -H X-Auth-Token:${TOKEN} -H "Content-Type: application/json" "http://${MONASCA_API_HOST}:8070/v2.0/metrics/statistics?name=cpu.system_perc&start_time=${START_TIME}&merge_metrics=True&statistics=avg,min,max,sum,count&period=3600" | python -m json.tool
echo

## Use notification methods ##
echo "> POST notification-methods"
PAYLOAD='{"type": "EMAIL", "name": "Robin E-Mail", "address": "robin@cloudcube.com.tw"}'
NOTIFY_ID=`curl -sS -X POST -H X-Auth-Token:${TOKEN} -H "Content-Type: application/json" -d "${PAYLOAD}" http://${MONASCA_API_HOST}:8070/v2.0/notification-methods | sed -E "s/^.*\"id\": \"([0-9a-z\-]*)\".*$/\1/"`
echo "> PAYLOAD: ${PAYLOAD}"
echo "> NOTIFY_ID: ${NOTIFY_ID}"
echo

echo "> GET notification-methods"
curl -sS -H X-Auth-Token:${TOKEN} -H "Content-Type: application/json" http://${MONASCA_API_HOST}:8070/v2.0/notification-methods | python -m json.tool
echo

## Use alarm definitions ##
echo "> POST alarm-definitions"
PAYLOAD='{"name": "high cpu usage", "expression": "max(cpu.system_perc{hostname='${HOST_NAME}'}) > 0", "alarm_actions": ["'$NOTIFY_ID'"], "ok_actions": ["'$NOTIFY_ID'"], "undetermined_actions": ["'$NOTIFY_ID'"], "description": "System CPU Utilization exceeds 0%"}'
ALARM_DEF_ID=`curl -sS -X POST -H X-Auth-Token:${TOKEN} -H "Content-Type: application/json" -d "${PAYLOAD}" http://${MONASCA_API_HOST}:8070/v2.0/alarm-definitions | sed -E "s/^.*\"id\": \"([0-9a-z\-]*)\".*$/\1/"`
echo "> PAYLOAD: ${PAYLOAD}"
echo "> ALARM_DEF_ID: ${ALARM_DEF_ID}"
echo

echo "> GET alarm-definitions"
curl -sS -H X-Auth-Token:${TOKEN} -H "Content-Type: application/json" http://${MONASCA_API_HOST}:8070/v2.0/alarm-definitions | python -m json.tool
echo

## Query alarm histroy ##
echo "> GET alarms?alarm_definition_id=$ALARM_DEF_ID"
curl -sS -H X-Auth-Token:${TOKEN} -H 'Content-Type: application/json' http://${MONASCA_API_HOST}:8070/v2.0/alarms?alarm_definition_id=$ALARM_DEF_ID
echo

echo "> GET alarms/state-history"
curl -sS -H X-Auth-Token:${TOKEN} -H 'Content-Type: application/json' http://${MONASCA_API_HOST}:8070/v2.0/alarms/state-history/
echo

# -----
echo "> DELETE notification-methods"
curl -sS -X DELETE -H X-Auth-Token:${TOKEN} -H "Content-Type: application/json" http://${MONASCA_API_HOST}:8070/v2.0/notification-methods/${NOTIFY_ID}
echo

echo "> DELETE alarm-definitions"
curl -sS -X DELETE -H X-Auth-Token:${TOKEN} -H "Content-Type: application/json" http://${MONASCA_API_HOST}:8070/v2.0/alarm-definitions/${ALARM_DEF_ID}
echo
