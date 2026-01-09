Imports System
Imports System.IO
Imports System.Security.Cryptography
Imports System.Text
Imports SixLabors.ImageSharp
Imports SixLabors.ImageSharp.PixelFormats
Imports SixLabors.ImageSharp.Processing
Imports SixLabors.ImageSharp.Formats.Gif

Module Program
    Sub Main(args As String())
        Dim hash As String = If(args.Length > 0, args(0), "ee591c4c530ed59e4a3d08eb48692cb46aaddaee")
        Dim outPath As String = If(args.Length > 1, args(1), Path.Combine(Environment.CurrentDirectory, "buttcoin.gif"))

        Dim frames As Integer = 24
        Dim cell As Integer = 18
        Dim grid As Integer = 16
        Dim w As Integer = grid * cell
        Dim h As Integer = grid * cell

        Dim seedBytes = SHA256.HashData(Encoding.UTF8.GetBytes(hash))

        Using img As New Image(Of Rgba32)(w, h)
            img.Metadata.GetGifMetadata().RepeatCount = 0

            RenderFrame(img, seedBytes, 0, grid, cell)
            img.Frames.RootFrame.Metadata.GetGifMetadata().FrameDelay = 6

            For f As Integer = 1 To frames - 1
                Using frame As New Image(Of Rgba32)(w, h)
                    RenderFrame(frame, seedBytes, f, grid, cell)
                    frame.Frames.RootFrame.Metadata.GetGifMetadata().FrameDelay = 6
                    img.Frames.AddFrame(frame.Frames.RootFrame)
                End Using
            Next

            Dim enc As New GifEncoder() With {.ColorTableMode = GifColorTableMode.Global}
            img.Save(outPath, enc)
        End Using

        Console.WriteLine(outPath)
    End Sub

    Private Sub RenderFrame(frame As Image(Of Rgba32),
                            seed As Byte(),
                            tick As Integer,
                            grid As Integer,
                            cell As Integer)

        Dim mixInput(seed.Length + 4 - 1) As Byte
        Buffer.BlockCopy(seed, 0, mixInput, 0, seed.Length)
        BitConverter.GetBytes(tick).CopyTo(mixInput, seed.Length)

        Dim bytes = SHA256.HashData(mixInput)

        Dim needed As Integer = grid * grid * 3
        Dim stream(needed - 1) As Byte
        Dim idx As Integer = 0
        Dim counter As Integer = 0

        While idx < needed
            Dim b2(bytes.Length + 4 - 1) As Byte
            Buffer.BlockCopy(bytes, 0, b2, 0, bytes.Length)
            BitConverter.GetBytes(counter).CopyTo(b2, bytes.Length)
            Dim chunk = SHA256.HashData(b2)

            Dim take As Integer = Math.Min(chunk.Length, needed - idx)
            Buffer.BlockCopy(chunk, 0, stream, idx, take)
            idx += take
            counter += 1
        End While

        Dim offset As Integer = (tick * 7) Mod stream.Length

        frame.Mutate(
            Sub(ctx)
                ctx.Clear(New Rgba32(10, 10, 12))

                Dim p As Integer = 0
                For y As Integer = 0 To grid - 1
                    For x As Integer = 0 To grid - 1
                        Dim i As Integer = (offset + p) Mod stream.Length
                        Dim r As Byte = stream(i)
                        Dim g As Byte = stream((i + 1) Mod stream.Length)
                        Dim b As Byte = stream((i + 2) Mod stream.Length)
                        p += 3

                        Dim c As New Rgba32(CByte((r \ 2) + 80), CByte((g \ 2) + 80), CByte((b \ 2) + 80))
                        ctx.Fill(c, New SixLabors.ImageSharp.Rectangle(x * cell, y * cell, cell, cell))
                    Next
                Next
            End Sub
        )
    End Sub
End Module
