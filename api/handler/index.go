package handler

import (
	"github.com/harrisbisset/uniworksite/views/layout"
	"github.com/labstack/echo"
)

type IndexHandler struct{}

func (i IndexHandler) HandleShow(c echo.Context) error {
	return Render(c, layout.Base())
}
