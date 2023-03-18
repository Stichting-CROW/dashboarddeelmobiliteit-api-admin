-- SELECT all municipalities user has access to
SELECT DISTINCT(UNNEST(data_owner_of_municipalities))
FROM organisation
WHERE 
organisation_id IN 
(
	(SELECT owner_organisation_id
	FROM user_account
	JOIN organisation
	USING(organisation_id)
	JOIN view_data_access
	ON organisation.organisation_id = granted_organisation_id
	WHERE user_id = 'sven.boor@gmail.com')
	UNION
	(SELECT owner_organisation_id
	FROM user_account
	JOIN organisation
	USING(organisation_id)
	JOIN view_data_access
	ON user_account.user_id = granted_user
	WHERE user_id = 'sven.boor@gmail.com')
)
OR 
organisation_id IN 
(
	SELECT organisation_id
	FROM user_account
	JOIN organisation
	USING(organisation_id)
	WHERE user_id = 'sven.boor@gmail.com'
);

SELECT *
FROM organisation
JOIN
(
	SELECT organisation_id, sum(value)
	FROM
	organisation
	JOIN
		(SELECT * 
		FROM stats_pre_process 
		WHERE date = '2022-07-01' 
		AND stat_description = 'number_of_vehicles_available' 
		AND system_id is null
		) q1
ON right(zone_ref, -4) = ANY(data_owner_of_municipalities)
WHERE
type_of_organisation = 'MUNICIPALITY'
GROUP BY organisation_id) q2
USING (organisation_id);