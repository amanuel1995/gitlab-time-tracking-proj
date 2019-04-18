#!/usr/bin/env bash

mrm ~~/stor/assets/gitlab-time-summary/jobasset.tgz

tar -czvf jobasset.tgz *

mput -p -f jobasset.tgz  ~~/stor/assets/gitlab-time-summary/jobasset.tgz

rm jobasset.tgz

