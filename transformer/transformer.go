// A really thin and error-prone wrapper around the AMP Cache Transforms used
// by the amppackager available at https://github.com/ampproject/amppackager/tree/releases/transformer

package main

import "C"

import (
	rpb "github.com/ampproject/amppackager/transformer/request"
	t "github.com/ampproject/amppackager/transformer"
)

//export Transform
func Transform(d *C.char, u *C.char, v *C.char) *C.char {
	url := C.GoString(u)
	rtv := C.GoString(v)
	html := C.GoString(d)

	var req *rpb.Request
	if len(url) == 0 {
		// If no URL is given the default list of transformers (containing 'absoluteurl'
		// and 'urlrewrite') can't be used
		transformers := []string{
			"nodecleanup",
			"stripjs",
			"metatag",
			"linktag",
			"ampboilerplate",
			"unusedextensions",
			"serversiderendering",
			"ampruntimecss",
			"transformedidentifier",
			"reorderhead",
		}

		req = &rpb.Request{
			Html: html,
			Rtv: rtv,
			Transformers: transformers,
		}

		req.Config = rpb.Request_TransformersConfig(rpb.Request_TransformersConfig_value["CUSTOM"])
	} else {
		req = &rpb.Request{
			Html: html,
			DocumentUrl: url,
			Rtv: rtv,
		}
	}

  out, _, err := t.Process(req)

  if err != nil {
    return C.CString(html)
	}

  return C.CString(out)
}

func main() {
}
