package main

import (
	"database/sql"
	"fmt"
	"os"
)

func ListDatabases() ([]string, error) {
	dbHost := os.Getenv("POSTGRES_HOST")
	dbPort := os.Getenv("POSTGRES_PORT")
	dbUser := os.Getenv("POSTGRES_USER")
	dbPassword := os.Getenv("POSTGRES_PASSWORD")

	dbName := os.Getenv("POSTGRES_DB")
	if dbName == "" {
		dbName = "postgres"
	}

	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		dbHost, dbPort, dbUser, dbPassword, dbName)

	if dbHost == "" || dbPort == "" || dbUser == "" || dbPassword == "" {
		return nil, fmt.Errorf("las variables de entorno POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD son obligatorias")
	}

	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, fmt.Errorf("error al abrir la conexión a la base de datos: %v", err)
	}
	defer db.Close()

	err = db.Ping()
	if err != nil {
		return nil, fmt.Errorf("error al conectar a la base de datos: %v", err)
	}

	fmt.Println("Conexión a PostgreSQL exitosa. Listando bases de datos:")

	rows, err := db.Query("SELECT datname FROM pg_database WHERE datistemplate = false;")
	if err != nil {
		return nil, fmt.Errorf("error al ejecutar la consulta: %v", err)
	}
	defer rows.Close()

	var databases []string
	var dbNameResult string
	for rows.Next() {
		err := rows.Scan(&dbNameResult)
		if err != nil {
			return nil, fmt.Errorf("error al escanear el resultado: %v", err)
		}
		databases = append(databases, dbNameResult)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error después de iterar los resultados: %v", err)
	}

	return databases, nil
}
