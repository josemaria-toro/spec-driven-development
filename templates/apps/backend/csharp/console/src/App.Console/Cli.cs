using System.Collections.Generic;
using System.IO;

using App.Application;

namespace App.Console;

/// <summary>The command line interface of the application.</summary>
public static class Cli
{
    /// <summary>The exit code of a successful run.</summary>
    public const int Success = 0;

    /// <summary>The exit code of a run with invalid arguments.</summary>
    public const int UsageError = 2;

    /// <summary>The usage message written to the error stream.</summary>
    public const string Usage = "Usage: App.Console [name]";

    /// <summary>Runs the application with the given arguments.</summary>
    /// <param name="arguments">The command line arguments: none or one name.</param>
    /// <param name="output">Where the result is written.</param>
    /// <param name="errors">Where usage errors are written.</param>
    /// <returns>The exit code.</returns>
    public static int Run(IReadOnlyList<string> arguments, TextWriter output, TextWriter errors)
    {
        if (arguments.Count > 1)
        {
            errors.WriteLine(Usage);
            return UsageError;
        }

        output.WriteLine(GreetUseCase.Execute(arguments.Count == 0 ? string.Empty : arguments[0]));
        return Success;
    }
}
