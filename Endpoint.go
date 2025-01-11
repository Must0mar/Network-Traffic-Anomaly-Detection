package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
)

type EmailList struct {
	Emails []string `json:"emails"`
}

func enableCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusOK)
			return
		}
		next.ServeHTTP(w, r)
	})
}

func main() {
	emailFile := "emails.json"
	trafficFile := "network_traffic_summary.json"
	alertFile := "alert.json"

	http.Handle("/emails", enableCORS(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			file, err := os.Open(emailFile)
			if err != nil {
				http.Error(w, "Error reading email file", http.StatusInternalServerError)
				fmt.Println("Error opening file:", err)
				return
			}
			defer file.Close()

			data, err := ioutil.ReadAll(file)
			if err != nil {
				http.Error(w, "Error reading file content", http.StatusInternalServerError)
				fmt.Println("Error reading file content:", err)
				return
			}

			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			w.Write(data)

		case http.MethodPost:
			var emailList EmailList
			if err := json.NewDecoder(r.Body).Decode(&emailList); err != nil {
				http.Error(w, "Invalid JSON format", http.StatusBadRequest)
				fmt.Println("Invalid JSON format:", err)
				return
			}

			data, err := json.MarshalIndent(emailList, "", "  ")
			if err != nil {
				http.Error(w, "Error encoding email data", http.StatusInternalServerError)
				fmt.Println("Error encoding email data:", err)
				return
			}

			if err := ioutil.WriteFile(emailFile, data, 0644); err != nil {
				http.Error(w, "Error saving email data", http.StatusInternalServerError)
				fmt.Println("Error writing to file:", err)
				return
			}

			w.WriteHeader(http.StatusOK)
			w.Write([]byte("Email list updated successfully"))

		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})))

	http.Handle("/get-data", enableCORS(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		file, err := os.Open(trafficFile)
		if err != nil {
			http.Error(w, "Error reading JSON file", http.StatusInternalServerError)
			fmt.Println("Error opening file:", err)
			return
		}
		defer file.Close()

		data, err := ioutil.ReadAll(file)
		if err != nil {
			http.Error(w, "Error reading file content", http.StatusInternalServerError)
			fmt.Println("Error reading file content:", err)
			return
		}

		var parsedData interface{}
		if err := json.Unmarshal(data, &parsedData); err != nil {
			http.Error(w, "Invalid JSON format", http.StatusInternalServerError)
			fmt.Println("Invalid JSON format:", err)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)

		w.Write(data)
	})))

	http.Handle("/alert", enableCORS(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodGet {
			file, err := os.Open(alertFile)
			if err != nil {
				http.Error(w, "Error reading alert file", http.StatusInternalServerError)
				fmt.Println("Error opening file:", err)
				return
			}
			defer file.Close()

			data, err := ioutil.ReadAll(file)
			if err != nil {
				http.Error(w, "Error reading file content", http.StatusInternalServerError)
				fmt.Println("Error reading file content:", err)
				return
			}

			var parsedData interface{}
			if err := json.Unmarshal(data, &parsedData); err != nil {
				http.Error(w, "Invalid JSON format", http.StatusInternalServerError)
				fmt.Println("Invalid JSON format:", err)
				return
			}

			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)

			w.Write(data)
		} else {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})))

	port := ":8080"
	fmt.Println("Server is running on port", port)
	if err := http.ListenAndServe(port, nil); err != nil {
		fmt.Println("Error starting server:", err)
	}
}
