hash go 2>/dev/null || { echo >&2 "Go is required to built django-amp."; exit 1; }
go get github.com/karalabe/xgo

hash xgo 2>/dev/null || { echo >&2 "xgo could not be found in your $PATH."; exit 1; }

xgo --targets="darwin/amd64,linux/amd64" --pkg transformer --buildmode=c-shared -out amp/lib/transformer github.com/matthiasrohmer/django-amp
