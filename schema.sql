CREATE TABLE populations(
	city VARCHAR (50) NOT NULL,
	population INT NOT NULL,
	PRIMARY KEY (city)
);

SELECT cd.age,
	cd.gender,
	cd.size,
	cd.status_changed_at,
	cd.published_at,
	cd.breeds_primary,
	cd.breeds_mixed,
	cd.breeds_unknown,
	cd.spayed_neutered,
	cd.house_trained,
	cd.special_needs,
	cd.shots_current,
	cd.location,
	po.population
INTO learning_table
FROM clean_dog_adoptions as cd
LEFT JOIN populations as po
ON cd.location = po.city;