#!/bin/bash
yum update -y
yum install -y python3-pip git
pip3 install "urllib3<2.0" locust
HOME_DIR="/home/ec2-user"

cat << 'PY_EOF' > $HOME_DIR/locustfile.py
import random
from locust import HttpUser, task, between
class WordPressUser(HttpUser):
   wait_time = between(1, 3)
   @task(3)
   def view_home(self): self.client.get("/")
   @task(10)
   def view_post(self): self.client.get(f"/post-{random.randint(1, 100)}/", name="/post-detail")
PY_EOF

cat << 'SH_EOF' > $HOME_DIR/wrapper.sh
#!/bin/bash
rm -f dados_*.csv
TARGET=$1
USERS=$2
DURATION=${3:-5m}
SPAWN_RATE=$(($USERS / 10))
[ "$SPAWN_RATE" -lt 1 ] && SPAWN_RATE=1
locust -f locustfile.py --headless --host "$TARGET" --users "$USERS" --spawn-rate "$SPAWN_RATE" --run-time "$DURATION" --stop-timeout 10 --csv dados --only-summary
SH_EOF

chown -R ec2-user:ec2-user $HOME_DIR
chmod +x $HOME_DIR/wrapper.sh
