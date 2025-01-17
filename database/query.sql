CREATE TABLE IF NOT EXISTS buttons
(
    id         SERIAL PRIMARY KEY,
    text       VARCHAR(40) NOT NULL,
    key        VARCHAR(50) unique NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users
(
    id         SERIAL PRIMARY KEY,
    user_id    BIGINT NOT NULL unique,
    status user_status_enum DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resources
(
    id        SERIAL PRIMARY KEY,
    button_key VARCHAR NOT NULL,
    url   TEXT           DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS channels
(
    id           SERIAL PRIMARY KEY,
    channel_id   BIGINT  NOT NULL,
    channel_link VARCHAR NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings
(
    id         SERIAL PRIMARY KEY,
    name       VARCHAR NOT NULL,
    value      VARCHAR NOT NULL,
    created_at TIMESTAMP default CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS join_requests
(
    id      SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS mailing
(
    id           BIGSERIAL PRIMARY KEY,
    status       BOOLEAN   NOT NULL DEFAULT TRUE,
    user_id      BIGINT,
    message_id   BIGINT,
    reply_markup TEXT,
    mail_type    TEXT      NOT NULL,
    "offset"     BIGINT    NOT NULL DEFAULT 0,
    send         BIGINT    NOT NULL DEFAULT 0,
    not_send     BIGINT    NOT NULL DEFAULT 0,
    "type"       TEXT      NOT NULL,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);