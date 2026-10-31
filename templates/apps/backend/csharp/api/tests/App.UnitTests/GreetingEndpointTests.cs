using System.Linq;

using App.Api;

using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Http.HttpResults;

using Xunit;

namespace App.UnitTests;

public sealed class GreetingEndpointTests
{
    private static readonly GreeterService Greeter = new();

    [Fact]
    public void Handle_WithAValidName_ReturnsTheGreeting()
    {
        var result = GreetingEndpoint.Handle("Ada", Greeter);

        var ok = Assert.IsType<Ok<GreetingResponse>>(result);
        Assert.Equal("Hello, Ada!", ok.Value?.Message);
    }

    [Fact]
    public void Handle_WithTheLongestName_IsAccepted()
    {
        var result = GreetingEndpoint.Handle(new string('a', GreetingEndpoint.MaxNameLength), Greeter);

        Assert.IsType<Ok<GreetingResponse>>(result);
    }

    [Fact]
    public void Handle_WithANameThatIsTooLong_ReturnsAValidationProblemNamingTheField()
    {
        var name = new string('a', GreetingEndpoint.MaxNameLength + 1);

        var result = GreetingEndpoint.Handle(name, Greeter);

        var problem = Assert.IsType<ProblemHttpResult>(result);
        var details = Assert.IsType<HttpValidationProblemDetails>(problem.ProblemDetails);
        Assert.Equal(StatusCodes.Status400BadRequest, problem.StatusCode);
        Assert.Equal(["name"], details.Errors.Keys.ToArray());
        Assert.DoesNotContain(name, string.Join(' ', details.Errors.Values.SelectMany(error => error)));
    }

    [Fact]
    public void Greet_UsesTheApplicationUseCase()
    {
        Assert.Equal("Hello, Ada!", Greeter.Greet(" Ada "));
    }
}
