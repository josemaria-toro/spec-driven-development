using App.Application;

using Xunit;

namespace App.IntegrationTests;

public sealed class GreetIntegrationTests
{
    [Fact]
    public void Greet_ThroughThePublicApi_GoesThroughTheDomain()
    {
        Assert.Equal("Hello, Ada!", GreetUseCase.Execute("Ada"));
    }
}
