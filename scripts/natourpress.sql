CREATE DATABASE  `natourpress` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;

CREATE USER 'natourpress'@'localhost' IDENTIFIED BY  'natourpress';

GRANT ALL PRIVILEGES ON * . * TO  'natourpress'@'localhost' IDENTIFIED BY  'natourpress' 
WITH GRANT OPTION MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;

GRANT ALL PRIVILEGES ON  `natourpress` . * TO  'natourpress'@'localhost';
