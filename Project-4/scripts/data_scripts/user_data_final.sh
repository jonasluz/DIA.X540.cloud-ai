#!/bin/bash
# user_data_template.sh
# Este script roda na inicialização de cada instância da Aplicação.


# --- 1. INSTALAÇÃO DE PACOTES ---
yum update -y
amazon-linux-extras install -y lamp-mariadb10.2-php7.2 php7.2
yum install -y httpd git


# --- 2. CONFIGURAÇÃO DE SERVIÇO (AREA DE TUNING) ---
systemctl start httpd
systemctl enable httpd


# DICA: Adicione aqui comandos de otimização (ex: alterar httpd.conf)
# Tunning do Apache (Prefork MPM) - Limitando para evitar OOM em t3.micro (1GB RAM)
echo "ServerLimit 30" >> /etc/httpd/conf/httpd.conf
echo "MaxRequestWorkers 30" >> /etc/httpd/conf/httpd.conf


# --- 3. INSTALAÇÃO DO WORDPRESS (NÃO ALTERAR ABAIXO) ---
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar
mv wp-cli.phar /usr/local/bin/wp


cd /var/www/html
wp core download --allow-root


# O script de deploy substituirá os PLACEHOLDERS pelos valores reais
wp config create --dbname=wordpress --dbuser=wp_user --dbpass=wp_pass --dbhost=10\.0\.1\.221 --allow-root


# Correção de configuração do Apache para permitir .htaccess
cat <<CONF > /etc/httpd/conf.d/wp-override.conf
<Directory "/var/www/html">
   AllowOverride All
</Directory>
CONF


# Configuração de Permalinks e Permissões
chown -R apache:apache /var/www/html
wp rewrite structure '/%postname%/' --hard --allow-root


# Criação forçada do .htaccess
cat <<HTACCESS > /var/www/html/.htaccess
# BEGIN WordPress
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
RewriteBase /
RewriteRule ^index\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.php [L]
</IfModule>
# END WordPress
HTACCESS


# Ajuste final de URLs para o Load Balancer
wp option update home 'http://BenchmarkALB-1439280466\.us-east-1\.elb\.amazonaws\.com' --allow-root
wp option update siteurl 'http://BenchmarkALB-1439280466\.us-east-1\.elb\.amazonaws\.com' --allow-root
chown apache:apache /var/www/html/.htaccess
chmod 644 /var/www/html/.htaccess


systemctl restart httpd





