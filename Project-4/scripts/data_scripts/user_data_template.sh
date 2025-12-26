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

# ----------------------------------------------------------------------
# TUNING DO APACHE (MPM Prefork)
# Ajuste conforme o cenário de hardware (vCPU/RAM)
# ----------------------------------------------------------------------
# Exemplo para 2 vCPU / 4GB RAM (Cenário 3 Tuned):
# MaxRequestWorkers 60 (evita CPU thrashing)
# ServerLimit 60
cat <<EOF >> /etc/httpd/conf/httpd.conf
<IfModule mpm_prefork_module>
    StartServers             5
    MinSpareServers          5
    MaxSpareServers         10
    MaxRequestWorkers       60
    ServerLimit             60
</IfModule>
EOF

# ----------------------------------------------------------------------
# TUNING DO PHP (OPcache)
# Ajuste para usar memória excedente como cache
# ----------------------------------------------------------------------
# Cria arquivo de configuração customizado para o PHP
# cat <<EOF > /etc/php.d/99-tuning.ini
# [opcache]
# opcache.enable=1
# opcache.memory_consumption=512
# opcache.interned_strings_buffer=64
# opcache.max_accelerated_files=20000
# opcache.validate_timestamps=0
# EOF


# --- 3. INSTALAÇÃO DO WORDPRESS (NÃO ALTERAR ABAIXO) ---
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar
mv wp-cli.phar /usr/local/bin/wp


cd /var/www/html
wp core download --allow-root


# O script de deploy substituirá os PLACEHOLDERS pelos valores reais
wp config create --dbname=wordpress --dbuser=wp_user --dbpass=wp_pass --dbhost=PLACEHOLDER_DB_IP --allow-root


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
wp option update home 'http://PLACEHOLDER_LB_DNS' --allow-root
wp option update siteurl 'http://PLACEHOLDER_LB_DNS' --allow-root
chown apache:apache /var/www/html/.htaccess
chmod 644 /var/www/html/.htaccess


systemctl restart httpd

