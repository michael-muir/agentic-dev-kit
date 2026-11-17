package demo_test

import (
	"testing"

	"example.com/demo"
)

func TestAdd(t *testing.T) {
	t.Run("DEMO-AC-1 adds two integers", func(t *testing.T) {
		if got, want := demo.Add(2, 3), 5; got != want {
			t.Fatalf("got %d, want %d", got, want)
		}
	})
}
