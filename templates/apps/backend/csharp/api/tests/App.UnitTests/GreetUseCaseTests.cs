using App.Application;

using Xunit;

namespace App.UnitTests;

public sealed class GreetUseCaseTests
{
    [Fact]
    public void Execute_WhenGivenAName_UsesTheDomainRule()
    {
        Assert.Equal("Hello, Ada!", GreetUseCase.Execute(" Ada "));
    }
}
