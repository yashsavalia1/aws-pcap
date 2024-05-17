package dashboard

import (
	"fmt"
	"log"
	"net/url"
	"os"
	"os/exec"
	"slices"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

/* var (
	//go:embed dist/*
	dist embed.FS

	//go:embed dist/index.html
	indexHTML embed.FS

	distDirFS     = echo.MustSubFS(dist, "dist")
	distIndexHTML = echo.MustSubFS(indexHTML, "dist")
) */

func RegisterHandlers(e *echo.Echo) {
	if slices.Contains(os.Args, "--prod") {
		e.Use(middleware.StaticWithConfig(middleware.StaticConfig{
			Root:   "dashboard/dist",
			Browse: true,
			HTML5:  true,
			Skipper: func(c echo.Context) bool {
				// Skip if the prefix is /api
				return len(c.Request().RequestURI) >= 4 && c.Request().RequestURI[:4] == "/api"
			},
		}))
	} else {
		fmt.Println("Running in dev mode")
		setupDevProxy(e)
	}
}

func setupDevProxy(e *echo.Echo) {
	// start the vite dev server
	cmd := exec.Command("npm", "run", "dev")
	cmd.Dir = "dashboard"
	err := cmd.Start()
	if err != nil {
		log.Fatal(err)
	}

	url, err := url.Parse("http://localhost:5173")
	if err != nil {
		log.Fatal(err)
	}
	// Setup a proxy to the vite dev server on localhost:5173
	balancer := middleware.NewRoundRobinBalancer([]*middleware.ProxyTarget{
		{
			URL: url,
		},
	})
	e.Use(middleware.ProxyWithConfig(middleware.ProxyConfig{
		Balancer: balancer,
		Skipper: func(c echo.Context) bool {
			// Skip the proxy if the prefix is /api
			return len(c.Request().RequestURI) >= 4 && c.Request().RequestURI[:4] == "/api"
		},
	}))
}
