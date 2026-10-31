using System;
using System.Diagnostics;
using System.IO;

using App.Console;

using Xunit;

namespace App.IntegrationTests;

public sealed class ConsoleProcessTests
{
    [Fact]
    public void Run_WithOneName_WritesTheGreetingAndExitsWithZero()
    {
        var result = RunExecutable("Ada");

        Assert.Equal(0, result.ExitCode);
        Assert.Equal("Hello, Ada!", result.Output.Trim());
        Assert.Empty(result.Errors);
    }

    [Fact]
    public void Run_WithTooManyArguments_WritesTheUsageToStandardErrorOnly()
    {
        var result = RunExecutable("Ada", "Grace");

        Assert.Equal(Cli.UsageError, result.ExitCode);
        Assert.Empty(result.Output);
        Assert.Contains(Cli.Usage, result.Errors);
        Assert.DoesNotContain("   at ", result.Errors);
    }

    private static (int ExitCode, string Output, string Errors) RunExecutable(params string[] arguments)
    {
        var assembly = Path.Combine(
            Path.GetDirectoryName(typeof(Cli).Assembly.Location)!,
            typeof(Cli).Assembly.GetName().Name + ".dll");
        var host = Environment.ProcessPath ?? throw new InvalidOperationException("No host process.");
        var start = new ProcessStartInfo(host)
        {
            RedirectStandardError = true,
            RedirectStandardOutput = true,
        };
        start.ArgumentList.Add(assembly);
        foreach (var argument in arguments)
        {
            start.ArgumentList.Add(argument);
        }

        using var process = Process.Start(start) ?? throw new InvalidOperationException("No process.");
        var output = process.StandardOutput.ReadToEnd();
        var errors = process.StandardError.ReadToEnd();
        process.WaitForExit();
        return (process.ExitCode, output, errors);
    }
}
