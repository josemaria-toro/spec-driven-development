using System;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;

using App.Api;

using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;

using Xunit;

namespace App.IntegrationTests;

public sealed class ApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private static readonly Uri BaseAddress = new("https://example.test");

    private readonly WebApplicationFactory<Program> _factory;

    public ApiTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory.WithWebHostBuilder(builder => builder.UseEnvironment("Production"));
    }

    [Fact]
    public async Task Get_WithAValidName_ReturnsTheGreetingWithSecurityHeaders()
    {
        using var client = CreateClient(_factory);

        using var response = await client.GetAsync(new Uri("/greetings/Ada", UriKind.Relative));

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var body = await response.Content.ReadFromJsonAsync<GreetingResponse>();
        Assert.Equal("Hello, Ada!", body?.Message);
        Assert.Equal("nosniff", response.Headers.GetValues("X-Content-Type-Options").Single());
        Assert.Equal("DENY", response.Headers.GetValues("X-Frame-Options").Single());
        Assert.True(response.Headers.Contains("Strict-Transport-Security"));
    }

    [Fact]
    public async Task Get_WithANameThatIsTooLong_ReturnsAClientErrorNamingTheField()
    {
        using var client = CreateClient(_factory);
        var name = new string('a', GreetingEndpoint.MaxNameLength + 1);

        using var response = await client.GetAsync(new Uri($"/greetings/{name}", UriKind.Relative));

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        Assert.Equal("application/problem+json", response.Content.Headers.ContentType?.MediaType);
        var text = await response.Content.ReadAsStringAsync();
        Assert.Contains("\"name\"", text, StringComparison.Ordinal);
        Assert.DoesNotContain(name, text, StringComparison.Ordinal);
    }

    [Fact]
    public async Task Get_WhenTheUseCaseFails_ReturnsAGenericServerError()
    {
        using var failing = _factory.WithWebHostBuilder(builder =>
            builder.ConfigureTestServices(services => services.AddSingleton<IGreeter, FailingGreeter>()));
        using var client = CreateClient(failing);

        using var response = await client.GetAsync(new Uri("/greetings/Ada", UriKind.Relative));

        Assert.Equal(HttpStatusCode.InternalServerError, response.StatusCode);
        var text = await response.Content.ReadAsStringAsync();
        Assert.DoesNotContain("secret detail", text, StringComparison.Ordinal);
        Assert.DoesNotContain(nameof(InvalidOperationException), text, StringComparison.Ordinal);
        Assert.DoesNotContain("   at ", text, StringComparison.Ordinal);
        Assert.Equal("nosniff", response.Headers.GetValues("X-Content-Type-Options").Single());
    }

    private static HttpClient CreateClient(WebApplicationFactory<Program> factory) =>
        factory.CreateClient(new WebApplicationFactoryClientOptions { BaseAddress = BaseAddress });

    private sealed class FailingGreeter : IGreeter
    {
        public string Greet(string name) => throw new InvalidOperationException("secret detail");
    }
}
