package main

import (
	"bytes"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"time"
)

type OdooBackupConfig struct {
	OdooURL        string
	MasterPassword string
	BackupFormat   string
	OutputDir      string
}

func backupAllDatabases() ([]string, error) {
	list, err := ListDatabases()
	if err != nil {
		return nil, fmt.Errorf("error al listar bases de datos: %v", err)
	}

	config := OdooBackupConfig{
		OdooURL:        os.Getenv("ADMIN_URL"),
		MasterPassword: os.Getenv("ADMIN_PASSWORD"),
		BackupFormat:   os.Getenv("ODOO_BACKUP_FORMAT"),
		OutputDir:      os.Getenv("ODOO_BACKUP_PATH"),
	}

	var backups []string

	for _, dbName := range list {
		if dbName == "postgres" || dbName == "template0" || dbName == "template1" {
			continue
		}

		log.Printf("Iniciando backup de la base de datos: %s", dbName)

		backupPath, err := BackupOdooDatabase(dbName, config)
		if err != nil {
			log.Printf("Error al hacer backup de la base de datos '%s': %v", dbName, err)
			continue
		}
		backups = append(backups, backupPath)
	}

	return backups, nil
}

func BackupOdooDatabase(dbName string, config OdooBackupConfig) (string, error) {
	if config.OdooURL == "" || config.MasterPassword == "" || dbName == "" {
		return "", fmt.Errorf("OdooURL, MasterPassword y dbName no pueden estar vacíos")
	}

	if config.BackupFormat == "" {
		config.BackupFormat = "zip"
	}

	if config.OutputDir == "" {
		config.OutputDir = os.TempDir()
		log.Printf("Advertencia: OutputDir no especificado, usando: %s", config.OutputDir)
	}

	backupEndpoint := fmt.Sprintf("%s/web/database/backup", config.OdooURL)

	form := fmt.Sprintf("master_pwd=%s&name=%s&backup_format=%s", config.MasterPassword, dbName, config.BackupFormat)
	log.Printf("Iniciando backup para la DB '%s' en %s", dbName, config.OdooURL)

	req, err := http.NewRequest("POST", backupEndpoint, bytes.NewBufferString(form))
	if err != nil {
		return "", fmt.Errorf("error al crear la petición HTTP: %w", err)
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Accept", "application/octet-stream")

	client := &http.Client{Timeout: 10 * time.Minute}
	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("no se pudo hacer el backup de la base de datos '%s': %w", dbName, err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("error en la respuesta del servidor: %s - %s", resp.Status, string(bodyBytes))
	}

	backupFileName := fmt.Sprintf("%s_%s.%s", dbName, time.Now().Format("20060102_150405"), config.BackupFormat)
	fullPath := filepath.Join(config.OutputDir, dbName, backupFileName)

	if err := os.MkdirAll(filepath.Dir(fullPath), 0755); err != nil {
		return "", fmt.Errorf("error al crear directorio '%s': %w", filepath.Dir(fullPath), err)
	}

	outFile, err := os.Create(fullPath)
	if err != nil {
		return "", fmt.Errorf("error al crear archivo '%s': %w", fullPath, err)
	}
	defer outFile.Close()

	n, err := io.Copy(outFile, resp.Body)
	if err != nil {
		return "", fmt.Errorf("error al guardar backup: %w", err)
	}

	log.Printf("Backup exitoso: '%s' (%d bytes)", fullPath, n)
	return fullPath, nil
}
