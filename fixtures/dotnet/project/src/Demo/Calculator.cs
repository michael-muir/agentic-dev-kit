namespace Demo;

/// <summary>Performs integer arithmetic for the fixture tests.</summary>
public static class Calculator
{
    /// <summary>Adds two integers.</summary>
    /// <param name="left">The first addend.</param>
    /// <param name="right">The second addend.</param>
    /// <returns>The sum of <paramref name="left"/> and <paramref name="right"/>.</returns>
    public static int Add(int left, int right)
    {
        return left + right;
    }
}
