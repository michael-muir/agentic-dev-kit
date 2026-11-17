namespace Demo.Tests;

public sealed class CalculatorTests
{
    [Fact]
    public void DEMO_AC_1_AddsTwoIntegers()
    {
        Assert.Equal(5, Calculator.Add(2, 3));
    }
}
