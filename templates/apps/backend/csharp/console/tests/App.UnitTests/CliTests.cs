using System.IO;

using App.Console;

using Xunit;

namespace App.UnitTests;

public sealed class CliTests
{
    [Fact]
    public void Run_WithOneName_WritesTheGreetingAndSucceeds()
    {
        using var output = new StringWriter();
        using var errors = new StringWriter();

        var exitCode = Cli.Run(["Ada"], output, errors);

        Assert.Equal(Cli.Success, exitCode);
        Assert.Equal("Hello, Ada!" + output.NewLine, output.ToString());
        Assert.Empty(errors.ToString());
    }

    [Fact]
    public void Run_WithoutArguments_GreetsTheDefaultName()
    {
        using var output = new StringWriter();
        using var errors = new StringWriter();

        var exitCode = Cli.Run([], output, errors);

        Assert.Equal(Cli.Success, exitCode);
        Assert.Equal("Hello, world!" + output.NewLine, output.ToString());
    }

    [Fact]
    public void Run_WithTooManyArguments_WritesTheUsageToTheErrorStreamOnly()
    {
        using var output = new StringWriter();
        using var errors = new StringWriter();

        var exitCode = Cli.Run(["Ada", "Grace"], output, errors);

        Assert.Equal(Cli.UsageError, exitCode);
        Assert.Empty(output.ToString());
        Assert.Contains(Cli.Usage, errors.ToString());
    }
}
