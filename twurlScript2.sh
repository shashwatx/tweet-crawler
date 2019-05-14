#!/usr/bin/env bash

id=${1}

#rm -rf problems.json

twurl /1.1/statuses/show.json?id=${id} | jq --arg id "${id}" 'if errors==null then {id: .id_str, date: .created_at, text: .text} end else {id: ${id}, date: unknown, text: unknown' >> problems.json
