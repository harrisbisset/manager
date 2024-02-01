package main

import (
	"log"
	"log/slog"
	"net/http"
	"os"
	"strconv"

	"github.com/harrisbisset/manager/api"
	"github.com/labstack/echo"
)

func main() {
	app := echo.New()
	port, strPort := getPort()
	logger := slog.Default()

	api := api.New(
		port,
		"",
		app,
		logger,
		// data.CreateConfig(),
	)

	api.SetRoutes()

	if err := api.GetApp().Start(strPort); err != http.ErrServerClosed {
		log.Fatal(err)
	}
}

func getPort() (int, string) {
	var port int
	var err error

	sPort := os.Getenv("PORT")
	if len(sPort) == 0 {
		sPort = ":3000"
		port = 3000
	} else {
		sPort = "0.0.0.0:" + sPort
		port, err = strconv.Atoi(sPort)
		if err != nil {
			log.Fatal(err)
		}
	}

	return port, sPort
}
