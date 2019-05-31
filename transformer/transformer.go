// A really thin and error-prone wrapper around the AMP Cache Transforms used
// by the amppackager available at https://github.com/ampproject/amppackager/tree/releases/transformer
package main

import "C"

import (
	rpb "github.com/ampproject/amppackager/transformer/request"
	t "github.com/ampproject/amppackager/transformer"
)

//export Transform
func Transform(data *C.char, url *C.char, rtv *C.char) *C.char {
  r := &rpb.Request{Html: C.GoString(data), DocumentUrl: C.GoString(url), Rtv: C.GoString(rtv)}
  o, _, err := t.Process(r)

  if err != nil {
    return C.CString(o)
	}

  return C.CString(o)
}

func main() {
}
