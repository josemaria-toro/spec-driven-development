using App.Domain;

using Xunit;

namespace App.UnitTests;

public sealed class GreetingTests
{
    [Theory]
    [InlineData("Ada", "Hello, Ada!")]
    [InlineData("  Ada  ", "Hello, Ada!")]
    [InlineData("", "Hello, world!")]
    [InlineData("   ", "Hello, world!")]
    public void Build_WhenGivenAName_ReturnsTheGreeting(string name, string expected)
    {
        Assert.Equal(expected, Greeting.Build(name));
    }
}
