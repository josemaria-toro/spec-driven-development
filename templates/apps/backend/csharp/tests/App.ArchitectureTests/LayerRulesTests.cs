using System.Reflection;

using App.Application;
using App.Domain;

using NetArchTest.Rules;

using Xunit;

namespace App.ArchitectureTests;

public sealed class LayerRulesTests
{
    private const string ApplicationNamespace = "App.Application";
    private const string InfrastructureNamespace = "App.Infrastructure";

    private static readonly string[] ForbiddenInTheCore =
    [
        "Microsoft.AspNetCore",
        "Microsoft.EntityFrameworkCore",
        "Npgsql",
        "RabbitMQ.Client",
        "System.Data",
        "System.Net.Http",
    ];

    private static readonly Assembly ApplicationAssembly = typeof(GreetUseCase).Assembly;
    private static readonly Assembly DomainAssembly = typeof(Greeting).Assembly;

    [Fact]
    public void Application_DoesNotDependOnInfrastructure()
    {
        var result = Types.InAssembly(ApplicationAssembly)
            .ShouldNot()
            .HaveDependencyOn(InfrastructureNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful, Describe(result));
    }

    [Fact]
    public void Domain_DoesNotDependOnOuterLayers()
    {
        var result = Types.InAssembly(DomainAssembly)
            .ShouldNot()
            .HaveDependencyOnAny(ApplicationNamespace, InfrastructureNamespace)
            .GetResult();

        Assert.True(result.IsSuccessful, Describe(result));
    }

    [Fact]
    public void DomainAndApplication_DoNotUseWebDatabaseBrokerOrHttpLibraries()
    {
        foreach (var assembly in new[] { DomainAssembly, ApplicationAssembly })
        {
            var result = Types.InAssembly(assembly)
                .ShouldNot()
                .HaveDependencyOnAny(ForbiddenInTheCore)
                .GetResult();

            Assert.True(result.IsSuccessful, Describe(result));
        }
    }

    private static string Describe(TestResult result) =>
        "Forbidden dependency in: " + string.Join(", ", result.FailingTypeNames ?? []);
}
