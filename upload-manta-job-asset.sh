#!/usr/bin/env bash

rm jobasset.tgz

tar -czvf jobasset.tgz *

mput -p -f jobasset.tgz  ~~/stor/assets/gitlab-time-summary/jobasset.tgz

rm jobasset.tgz

