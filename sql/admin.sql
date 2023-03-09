


CREATE TABLE organisation (
    organisation_id                 SERIAL PRIMARY KEY,
    name                            VARCHAR(255) NOT NULL UNIQUE,
    type_of_organisation            VARCHAR(30) NOT NULL, -- MUNICIPALITY, OTHER_GOVERNMENT, OPERATOR, ADMIN, OTHER_COMPANY
    data_owner_of_municipalities    VARCHAR(30)[], 
    data_owner_of_operators         VARCHAR(30)[],
    organisation_details            JSONB -- optional, only for municipalities,
);

INSERT INTO organisation (name, type_of_organisation)
VALUES ('CROW', 'ADMIN')
RETURNING organisation_id;

CREATE TABLE organisation_history (
    organisation_history_id       SERIAL PRIMARY KEY,
    organisation_id               INT NOT NULL,
    details                       JSONB,
    TIMESTAMP                     TIMESTAMP NOT NULL,
    CONSTRAINT fk_organisation_id
      FOREIGN KEY(organisation_id) 
	  REFERENCES organisation(organisation_id)
	  ON DELETE CASCADE
);

CREATE INDEX organisation_history_organisation_id_index
ON organisation_history (organisation_id);

CREATE TABLE user_account (
    user_id             VARCHAR(255) PRIMARY KEY,       -- =email
    privileges          VARCHAR(30)[],      -- ORGANISATION_ADMIN, MICROHUB_EDIT, DOWNLOAD_RAW_DATA, CORE_GROUP
    organisation_id     INT NOT NULL,
    CONSTRAINT fk_organisation_id
      FOREIGN KEY(organisation_id) 
	  REFERENCES organisation(organisation_id)
	  ON DELETE CASCADE
);

CREATE TABLE view_data_access (
    grant_view_data_id          SERIAL PRIMARY KEY,
    owner_organisation_id       INT NOT NULL,
    granted_organisation_id     INT,
    granted_user                VARCHAR(255),       
    CONSTRAINT fk_organisation_id
      FOREIGN KEY(owner_organisation_id) 
	  REFERENCES organisation(organisation_id)
	  ON DELETE CASCADE,
    CONSTRAINT fk_user_id
      FOREIGN KEY(granted_user)
      REFERENCES user_account(user_id)
      ON DELETE CASCADE,
    UNIQUE(owner_organisation_id, granted_organisation_id),
    UNIQUE(owner_organisation_id, granted_user)
);

CREATE INDEX view_data_access_owner_organisation_index
ON view_data_access (owner_organisation_id);

CREATE INDEX view_data_access_granted_organisation_index
ON view_data_access (granted_organisation_id);

CREATE INDEX view_data_access_granted_user_index
ON view_data_access (granted_user);